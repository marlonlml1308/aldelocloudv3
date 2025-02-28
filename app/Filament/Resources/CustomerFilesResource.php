<?php

namespace App\Filament\Resources;

use App\Filament\Resources\CustomerFilesResource\Pages;
use App\Filament\Resources\CustomerFilesResource\RelationManagers;
use App\Models\CustomerFiles;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use pxlrbt\FilamentExcel\Actions\Tables\ExportBulkAction;

class CustomerFilesResource extends Resource
{
    protected static ?string $model = CustomerFiles::class;

    protected static ?string $navigationIcon = 'heroicon-o-user-plus';
    protected static ?string $navigationGroup = 'Configuracion';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('customername')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('deliveryaddress')
                    ->maxLength(255)
                    ->default(null),
                Forms\Components\TextInput::make('deliveryremarks')
                    ->maxLength(255)
                    ->default(null),
                Forms\Components\TextInput::make('deliverycharge')
                    ->numeric()
                    ->default(null),
                Forms\Components\TextInput::make('phonenumber')
                    ->tel()
                    ->required()
                    ->numeric(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('customername')
                    ->label('Nombre del Cliente')
                    ->searchable()
                    ->disabledClick(),
                Tables\Columns\TextColumn::make('deliveryaddress')
                    ->label('# de Calle')
                    ->searchable()
                    ->disabledClick(),
                Tables\Columns\TextColumn::make('deliveryremarks')
                    ->label('Nombre de Calle')
                    ->searchable()
                    ->disabledClick(),
                Tables\Columns\TextColumn::make('deliverycharge')
                    ->label('Cargo de Entrega')
                    ->numeric()
                    ->sortable()
                    ->disabledClick(),
                Tables\Columns\TextColumn::make('phonenumber')
                    ->label('Telefono')
                    ->searchable()
                    ->disabledClick(),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creado')
                    ->dateTime()
                    ->sortable()
                    ->disabledClick()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->disabledClick()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                //
            ])
            ->actions([
                // Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     // Tables\Actions\DeleteBulkAction::make(),
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
            'index' => Pages\ListCustomerFiles::route('/'),
            'create' => Pages\CreateCustomerFiles::route('/create'),
            'edit' => Pages\EditCustomerFiles::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Cliente');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Clientes');
    }
}
