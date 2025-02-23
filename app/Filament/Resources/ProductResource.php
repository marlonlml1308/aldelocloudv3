<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ProductResource\Pages;
use App\Filament\Resources\ProductResource\RelationManagers;
use App\Models\Modules;
use App\Models\Products;
use App\Models\Taxes;
use Filament\Forms;
use Filament\Forms\Components\Grid;
use Filament\Forms\Components\Hidden;
use Filament\Forms\Components\Placeholder;
use Filament\Forms\Components\Section;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use pxlrbt\FilamentExcel\Actions\Tables\ExportBulkAction;
use Filament\Tables\Columns\CheckboxColumn;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Enums\FiltersLayout;
use Filament\Tables\Filters\SelectFilter;
use Filament\Tables\Filters\TernaryFilter;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;

class ProductResource extends Resource
{
    protected static ?string $model = Products::class;
    protected static ?string $navigationGroup = 'Menu';
    protected static ?string $navigationIcon = 'heroicon-o-shopping-cart';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Section::make('Detalles del Producto')->schema([
                    TextInput::make('menuitemtext')
                    ->label('Producto')
                    ->required()
                    ->maxLength(22)
                    ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                    ->rule(function (string $operation, ?Model $record = null) {
                        return function ($attribute, $value, $fail) use ($operation, $record) {
                            if ($value !== null) {
                                $query = DB::table('products')
                                    ->where('menuitemtext', $value);
                                if ($operation === 'edit' && $record) {
                                    $query->where('id', '!=', $record->id);
                                }
                                $exists = $query->exists();
                                if ($exists) {
                                    $fail('El nombre ya está en uso. Debe ser único.');}
                            }
                        };
                    }),
                    Select::make('menucategoryid')->label('Categoria')
                    ->required()
                    ->relationship('categories', 'menucategorytext', function ($query) {
                        $query->where('menucategoryinactive', '!=', true);
                    })
                    ->reactive(),
                    Select::make('menugroupid')->label('Grupo')
                    ->required()
                    ->relationship('groups', 'menugrouptext', function ($query) {
                        $query->where('menugroupinactive', '!=', true);
                    })
                    ->reactive(),
                    TextInput::make('defaultunitprice')
                    ->label('Precio Base')
                    ->numeric()
                    ->extraInputAttributes([
                        'step' => '0.01', // Permite valores con dos decimales
                        'min' => '0', // Evita números negativos
                        'maxlength' => '10', // Asegura que el usuario no escriba más de 8 caracteres
                    ])
                    ->required()
                    ->prefix('$')
                    ->reactive(),
                    Placeholder::make('price_with_tax')
                        ->label('Precio con Impuesto')
                        ->content(function (callable $get) {
                            // Obtiene el precio base
                            $basePrice = (float) $get('defaultunitprice');
                            // Suma los porcentajes de los impuestos si están activos
                            $taxTotal = 0;
                            if ($get('menuitemtaxable')) {
                                $taxTotal += \App\Models\Taxes::getTaxPercent(1);
                            }
                            if ($get('gstapplied')) {
                                $taxTotal += \App\Models\Taxes::getTaxPercent(2);
                            }
                            if ($get('liquortaxapplied')) {
                                $taxTotal += \App\Models\Taxes::getTaxPercent(3);
                            }
                            // Calcula el precio final
                            $final = $basePrice * (1 + ($taxTotal / 100));
                            return '$' . number_format($final, 2);
                        })
                        ->reactive(),
                        Select::make('displayindex')
                        ->label('Posicion')
                        ->required()
                        ->options(function (string $operation, ?Model $record = null, callable $get) {
                            // Obtén el ID del grupo seleccionado en el formulario
                            $selectedGroupId = $get('menugroupid');
                            $query = DB::table('products')
                                ->where('menugroupid', $selectedGroupId)
                                ->where('menuiteminactive', '!=', true)
                                ->pluck('displayindex');
                            if ($operation === 'edit' && $record) {
                                $query = $query->filter(fn ($value) => $value != $record->displayindex);
                            }
                            $allPossibleValues = range(-1, 31);
                            $availableValues = collect($allPossibleValues)
                                ->filter(function ($value) use ($query) {
                                    return !$query->contains($value);
                                })
                                ->mapWithKeys(function ($value) {
                                    return [$value => $value === -1
                                        ? 'Inactivo o subplatillo (-1)'
                                        : "Posición {$value}"];
                                })
                                ->toArray();
                            return $availableValues;
                        })
                        ->searchable()
                        ->preload(),
                        TextInput::make('barcode')
                        ->label('Barcode')
                        ->required()
                        ->maxLength(20)
                        ->rule(function (string $operation, ?Model $record = null) {
                            return function ($attribute, $value, $fail) use ($operation, $record) {
                                if ($value !== null) {
                                    $query = DB::table('products')
                                        ->where('barcode', $value);
                                    if ($operation === 'edit' && $record) {
                                        $query->where('id', '!=', $record->id);
                                    }
                                    $exists = $query->exists();
                                    if ($exists) {
                                        $fail('El barcode ya está en uso. Debe ser único.');}
                                }
                            };
                        }),
                        Select::make('menuitemtype')
                        ->label('Tipo de Producto')
                        ->options([
                            1 => 'Producto',
                            2 => 'Platillo Superior',
                        ])
                        ->default(1) // Valor por defecto "Producto"
                        ->required()
                        ->live() // Hace que el cambio se detecte en tiempo real
                        ->afterStateUpdated(function ($state, callable $set) {
                            if ($state == 2) { // Si es "Platillo Superior"
                                $set('displayindex', -1); // Cambia la posición a -1
                                $set('defaultunitprice', 0); // Cambia el precio a 0
                            }
                        }),
                        Select::make('menuitempopupheaderid')
                        ->label('Producto Padre')
                        ->options(fn ($get) => Products::where('barcode', '!=', $get('barcode')) // Excluye el producto actual
                            ->pluck('menuitemtext', 'barcode')
                            ->toArray())
                        ->searchable() // Permite buscar dentro del select
                        ->preload() // Carga los datos antes de abrir el select
                        ->nullable(), // Permite no seleccionar un valor

                        Grid::make(4)->schema([
                            Toggle::make('menuiteminactive')
                                ->label('Inactivo')
                                ->required(),
                            Toggle::make('orderbyweight')
                                ->label('Ordenar por Peso')
                                ->required(),
                            Toggle::make('bar')
                                ->label('Producto de Bar')
                                ->required(),
                            Toggle::make('menuiteminstock')
                                ->label('En Stock')
                                ->required()
                                ->default(true),
                        ]),
                ])->columns(3),
                Section::make('Impuestos')->schema([
                    Toggle::make('menuitemtaxable')
                    ->label(fn () => Taxes::getTaxName(1))
                    ->reactive(),
                    Toggle::make('gstapplied')
                        ->label(fn () => Taxes::getTaxName(2))
                        ->reactive(),
                    Toggle::make('liquortaxapplied')
                        ->label(fn () => Taxes::getTaxName(3))
                        ->reactive(),
                    Toggle::make('menuitemdiscountable')
                    ->label('Descontable')
                    ->required()
                    ->default(true)
                    ->inline(false),
                    Select::make('gaspump')
                    ->label('Exento de Impuestos')
                    ->required()
                    ->options( [
                        'NO' => 'NO',
                        'YES' => 'YES',
                    ])
                    ->default('NO'),
                ])->columns(3),
                Section::make('Precios')->schema([
                    TextInput::make('dineinprice')
                    ->label(fn () => Modules::getModuleName(1))
                    ->numeric()
                    ->maxLength(8) // Restringe la longitud del texto
                    ->prefix('$') // Agrega el símbolo de moneda
                    ->extraInputAttributes([
                        'step' => '0.01', // Permite valores con dos decimales
                        'min' => '0', // Evita números negativos
                        'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                    ])
                    ->live(),
                    Placeholder::make('price_with_tax')
                    ->label('Precio con Impuesto')
                    ->content(function (callable $get) {
                        // Obtiene el precio base
                        $basePrice = (float) $get('dineinprice');
                        // Suma los porcentajes de los impuestos si están activos
                        $taxTotal = 0;
                        if ($get('menuitemtaxable')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(1);
                        }
                        if ($get('gstapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(2);
                        }
                        if ($get('liquortaxapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(3);
                        }
                        // Calcula el precio final
                        $final = $basePrice * (1 + ($taxTotal / 100));
                        return '$' . number_format($final, 2);
                    })
                    ->reactive(),
                    TextInput::make('takeoutprice')
                    ->label(fn () => Modules::getModuleName(2))
                    ->numeric()
                    ->maxLength(8) // Restringe la longitud del texto
                    ->prefix('$') // Agrega el símbolo de moneda
                    ->extraInputAttributes([
                        'step' => '0.01', // Permite valores con dos decimales
                        'min' => '0', // Evita números negativos
                        'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                    ])
                    ->live(),
                    Placeholder::make('price_with_tax')
                    ->label('Precio con Impuesto')
                    ->content(function (callable $get) {
                        // Obtiene el precio base
                        $basePrice = (float) $get('takeoutprice');
                        // Suma los porcentajes de los impuestos si están activos
                        $taxTotal = 0;
                        if ($get('menuitemtaxable')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(1);
                        }
                        if ($get('gstapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(2);
                        }
                        if ($get('liquortaxapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(3);
                        }
                        // Calcula el precio final
                        $final = $basePrice * (1 + ($taxTotal / 100));
                        return '$' . number_format($final, 2);
                    })
                    ->reactive(),
                    TextInput::make('drivethruprice')
                    ->label(fn () => Modules::getModuleName(3))
                    ->numeric()
                    ->maxLength(8) // Restringe la longitud del texto
                    ->prefix('$') // Agrega el símbolo de moneda
                    ->extraInputAttributes([
                        'step' => '0.01', // Permite valores con dos decimales
                        'min' => '0', // Evita números negativos
                        'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                    ])
                    ->live(),
                    Placeholder::make('price_with_tax')
                    ->label('Precio con Impuesto')
                    ->content(function (callable $get) {
                        // Obtiene el precio base
                        $basePrice = (float) $get('drivethruprice');
                        // Suma los porcentajes de los impuestos si están activos
                        $taxTotal = 0;
                        if ($get('menuitemtaxable')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(1);
                        }
                        if ($get('gstapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(2);
                        }
                        if ($get('liquortaxapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(3);
                        }
                        // Calcula el precio final
                        $final = $basePrice * (1 + ($taxTotal / 100));
                        return '$' . number_format($final, 2);
                    })
                    ->reactive(),
                    TextInput::make('DeliveryPrice')
                    ->label(fn () => Modules::getModuleName(4))
                    ->numeric()
                    ->maxLength(8) // Restringe la longitud del texto
                    ->prefix('$') // Agrega el símbolo de moneda
                    ->extraInputAttributes([
                        'step' => '0.01', // Permite valores con dos decimales
                        'min' => '0', // Evita números negativos
                        'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                    ])
                    ->live(),
                    Placeholder::make('price_with_tax')
                    ->label('Precio con Impuesto')
                    ->content(function (callable $get) {
                        // Obtiene el precio base
                        $basePrice = (float) $get('DeliveryPrice');
                        // Suma los porcentajes de los impuestos si están activos
                        $taxTotal = 0;
                        if ($get('menuitemtaxable')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(1);
                        }
                        if ($get('gstapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(2);
                        }
                        if ($get('liquortaxapplied')) {
                            $taxTotal += \App\Models\Taxes::getTaxPercent(3);
                        }
                        // Calcula el precio final
                        $final = $basePrice * (1 + ($taxTotal / 100));
                        return '$' . number_format($final, 2);
                    })
                    ->reactive(),
                ])->columns(4),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                TextColumn::make('id'),
                TextColumn::make('menuitemtext')->label('Producto')
                ->searchable(),
                TextColumn::make('barcode')->label('Barcode')
                ->searchable()
                ->sortable(),
                TextColumn::make('groups.menugrouptext')
                ->label('Grupo')
                ->sortable(),
                CheckboxColumn::make('menuiteminactive')->label('Inactivo')
                ->disabled(),
                TextColumn::make('menuitemtaxable')
                ->label(fn () => Taxes::getTaxName(1)) // Obtiene el nombre del impuesto 1
                ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                ->disabled(),
                TextColumn::make('gstapplied')
                    ->label(fn () => Taxes::getTaxName(2)) // Obtiene el nombre del impuesto 2
                    ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                    ->disabled(),
                TextColumn::make('liquortaxapplied')
                    ->label(fn () => Taxes::getTaxName(3)) // Obtiene el nombre del impuesto 3
                    ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                    ->disabled(),
                    TextColumn::make('price_with_tax')
                    ->label('Precio con Impuesto')
                    ->formatStateUsing(fn($state) => '$' . number_format($state, 0)),
            ])
            ->filters([
                SelectFilter::make('Categoria')
                ->relationship('categories','menucategorytext')
                ->searchable()
                ->preload(),
                SelectFilter::make('Grupo')
                ->relationship('groups','menugrouptext')
                ->searchable()
                ->preload(),
                SelectFilter::make('tax_filter')
                ->label('Impuesto')
                ->options(self::getTaxOptions())
                ->default(null)
                ->query(function ($query, $state) {
                    if (empty($state)) return $query;
                    return $query->where(function ($q) use ($state) {
                        if (in_array(1, $state)) {
                            $q->orWhere('menuitemtaxable', 1);
                        }
                        if (in_array(2, $state)) {
                            $q->orWhere('gstapplied', 1);
                        }
                        if (in_array(3, $state)) {
                            $q->orWhere('liquortaxapplied', 1);
                        }
                    });
                }),
            ], layout: FiltersLayout::AboveContent)->filtersFormColumns(3)
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     Tables\Actions\DeleteBulkAction::make(),
                // ]),
                ExportBulkAction::make(),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListProducts::route('/'),
            'create' => Pages\CreateProduct::route('/create'),
            'edit' => Pages\EditProduct::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Producto');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Productos');
    }
    public static function getTaxOptions(): array
    {
        return Taxes::pluck('taxname', 'id')->toArray();
    }
    protected function mutateFormDataBeforeSave(array $data): array
    {
        // Aquí asignamos el precio base (almacenado en 'price_base') a la propiedad que se guarda en el modelo
        $data['defaultunitprice'] = $data['price_base'];
        return $data;
    }

}
