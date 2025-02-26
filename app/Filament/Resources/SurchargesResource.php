<?php

namespace App\Filament\Resources;

use App\Filament\Resources\SurchargesResource\Pages;
use App\Filament\Resources\SurchargesResource\RelationManagers;
use App\Models\Surcharges;
use Filament\Forms;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;

class SurchargesResource extends Resource
{
    protected static ?string $model = Surcharges::class;

    protected static ?string $navigationIcon = 'heroicon-o-squares-plus';
    protected static ?string $navigationGroup = 'Configuracion';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                TextInput::make('surchargetext')
                ->label('Nombre')
                ->required()
                ->maxLength(14)
                ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('surcharges')
                                ->where('surchargetext', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El nombre ya está en uso. Debe ser único.');}
                        }
                    };
                }),
                Toggle::make('surchargeinactive')
                    ->label('Inactivo')
                    ->inline(false)
                    ->required(),
                Select::make('surchargebasis')
                    ->required()
                    ->label('Tipo de Descuento')
                    ->options([
                        1 => 'Porcentaje',
                        2 => 'Efectivo',
                    ]),
                TextInput::make('surchargeamount')
                    ->label('Monto')
                    ->required()
                    ->numeric(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('surchargetext')
                ->label('Nombre')
                ->searchable(),
                Tables\Columns\IconColumn::make('surchargeinactive')
                    ->label('Inactivo')
                    ->boolean(),
                Tables\Columns\TextColumn::make('surchargebasis')
                    ->label('Tipo')
                    ->formatStateUsing(fn ($state) => match ($state) {
                        1, '1' => 'Porcentaje',
                        2, '2' => 'Efectivo',
                        default => $state,
                    })
                    ->sortable(),
                Tables\Columns\TextColumn::make('surchargeamount')
                    ->label('Monto')
                    ->numeric()
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    // Tables\Actions\DeleteBulkAction::make(),
                ]),
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
            'index' => Pages\ListSurcharges::route('/'),
            'create' => Pages\CreateSurcharges::route('/create'),
            'edit' => Pages\EditSurcharges::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Sobrecargo');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Sobrecargos');
    }
}
